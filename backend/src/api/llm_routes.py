"""
LLM API routes for processing profiles
Implements all endpoints for the LLM profile processing feature
"""
from flask import Blueprint, request, jsonify, send_file
from typing import Dict, Any
import time
import os

from src.models.result import ProcessingResult, ResultManager
from src.models.history import HistoryManager
from src.services.llm_service import get_llm_service
from src.services.profile_service import get_profile_service
from src.services.prompt_service import get_prompt_service
from src.services.file_service import get_file_service
from src.utils.validation import (
    ValidationError, ErrorHandler, RequestValidator,
    require_profile_id, require_result_id, require_text
)
from src.utils.logging import log_request_response, log_llm_request, log_llm_response, log_file_generation, log_profile_usage
from src.utils.timeout import get_timeout_for_text
from src.config import Config

# Create Blueprint
llm_bp = Blueprint('llm', __name__)
# Configuration
config = Config()

# Service instances will be initialized on first use
_llm_service = None
_profile_service = None
_prompt_service = None
_file_service = None
_result_manager = None
_history_manager = None


def get_services():
    """Get or initialize service instances"""
    global _llm_service, _profile_service, _prompt_service, _file_service, _result_manager, _history_manager
    
    if _profile_service is None:
        _profile_service = get_profile_service(config)
    if _prompt_service is None:
        _prompt_service = get_prompt_service(config)
    if _file_service is None:
        _file_service = get_file_service(config)
    if _result_manager is None:
        _result_manager = ResultManager()
    if _history_manager is None:
        _history_manager = HistoryManager()
    
    # LLM service is initialized only when needed (requires API key)
    if _llm_service is None:
        try:
            _llm_service = get_llm_service(config)
        except ValueError as e:
            # API key not configured, will handle in endpoints
            pass
    
    return {
        'llm_service': _llm_service,
        'profile_service': _profile_service,
        'prompt_service': _prompt_service,
        'file_service': _file_service,
        'result_manager': _result_manager,
        'history_manager': _history_manager
    }


@llm_bp.route('/process', methods=['POST'])
@log_request_response
def process_text():
    """POST /llm/process - Process text with a specific profile"""
    try:
        # Get services
        services = get_services()
        llm_service = services['llm_service']
        profile_service = services['profile_service']
        prompt_service = services['prompt_service']
        result_manager = services['result_manager']
        history_manager = services['history_manager']
        
        # Check if LLM service is available
        if llm_service is None:
            return ErrorHandler.create_error_response(
                code="LLM_SERVICE_UNAVAILABLE",
                message="LLM service is not configured. Please check your API key.",
                status_code=503
            )
        # Validate and extract request data
        data = RequestValidator.validate_and_get_process_data(request)
        profile_id = data['profile_id']
        text = data['text']
        parameters = data['parameters']
        
        # Validate profile exists
        if not profile_service.validate_profile_exists(profile_id):
            return ErrorHandler.handle_profile_not_found(profile_id)
        
        # Validate profile parameters
        valid, error_msg = profile_service.validate_profile_parameters(profile_id, parameters)
        if not valid:
            return ErrorHandler.create_error_response(
                code="VALIDATION_ERROR",
                message=error_msg,
                status_code=400
            )
        
        # Calculate timeout
        timeout = get_timeout_for_text(text, profile_id, config)
        
        # Log LLM request
        log_llm_request(profile_id, len(text), timeout)
        log_profile_usage(profile_id, len(text))
        
        # Render prompt
        try:
            prompt = prompt_service.render_prompt(profile_id, text, parameters)
        except Exception as e:
            return ErrorHandler.create_error_response(
                code="PROMPT_ERROR",
                message=f"Failed to render prompt: {str(e)}",
                status_code=400
            )
        
        # Process with LLM
        start_time = time.time()
        try:
            llm_result = llm_service.process_text(prompt, timeout)
        except TimeoutError:
            return ErrorHandler.handle_timeout_error(timeout, profile_id)
        except Exception as e:
            return ErrorHandler.handle_llm_error(str(e), config.LLM_PROVIDER)
        
        processing_time = time.time() - start_time
        
        # Check if LLM processing was successful
        if not llm_result.get('success', False):
            error_info = llm_result.get('error', {})
            log_llm_response(profile_id, False, processing_time)
            return ErrorHandler.create_error_response(
                code=error_info.get('code', 'LLM_ERROR'),
                message=error_info.get('message', 'LLM processing failed'),
                details=error_info.get('details'),
                status_code=500
            )
        
        # Log successful LLM response
        log_llm_response(profile_id, True, processing_time, llm_result.get('metadata', {}).get('tokens_used'))
        
        # Create processing result
        result = ProcessingResult.create(
            profile_id=profile_id,
            input_text=text,
            output_text=llm_result['output'],
            processing_time=processing_time,
            metadata=llm_result.get('metadata', {})
        )
        
        # Store result
        result_id = result_manager.store_result(result)
        
        # Add to history (using a default transcription ID for now)
        transcription_id = request.headers.get('X-Transcription-ID', 'default')
        history_manager.add_result_to_history(transcription_id, result)
        
        # Return success response
        return jsonify({
            "success": True,
            "profile_id": profile_id,
            "result_id": result_id,
            "output": result.output_text,
            "metadata": {
                "processing_time": processing_time,
                "tokens_used": result.get_tokens_used(),
                "model_used": result.get_model_used()
            },
            "created_at": result.created_at.isoformat() + 'Z'
        }), 200
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """GET /llm/profiles - Get all available profiles"""
    try:
        # Get services
        services = get_services()
        profile_service = services['profile_service']
        
        profiles = profile_service.get_all_profiles()
        
        return jsonify({
            "profiles": profiles
        }), 200
        
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/results/<result_id>', methods=['GET'])
def get_result(result_id: str):
    """GET /llm/results/{id} - Get a specific processing result"""
    try:
        # Get services
        services = get_services()
        result_manager = services['result_manager']
        
        # Validate result ID format
        require_result_id(result_id)
        
        # Get result
        result = result_manager.get_result(result_id)
        if not result:
            return ErrorHandler.handle_result_not_found(result_id)
        
        # Return result data
        return jsonify({
            "result_id": result.id,
            "profile_id": result.profile_id,
            "output": result.output_text,
            "metadata": {
                "processing_time": result.processing_time,
                "tokens_used": result.get_tokens_used(),
                "model_used": result.get_model_used()
            },
            "created_at": result.created_at.isoformat() + 'Z'
        }), 200
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/download/<result_id>', methods=['POST'])
def download_result(result_id: str):
    """POST /llm/download/{id} - Download result in specified format"""
    try:
        # Get services
        services = get_services()
        result_manager = services['result_manager']
        profile_service = services['profile_service']
        file_service = services['file_service']
        
        # Validate result ID format
        require_result_id(result_id)
        
        # Validate and extract request data
        data = RequestValidator.validate_and_get_download_data(request)
        format_type = data['format']
        filename = data['filename']
        
        # Get result
        result = result_manager.get_result(result_id)
        if not result:
            return ErrorHandler.handle_result_not_found(result_id)
        
        # Generate file
        try:
            # Create title for document
            profile = profile_service.get_profile(result.profile_id)
            title = f"AudioLetra - {profile.name if profile else 'Resultado'}"
            
            file_path, content_type = file_service.generate_file(
                content=result.output_text,
                format_type=format_type,
                base_filename=filename,
                title=title
            )
            
            # Return file
            response = send_file(
                file_path,
                mimetype=content_type,
                as_attachment=True,
                download_name=filename
            )
            
            # Schedule file cleanup (after response is sent)
            @response.call_on_close
            def cleanup_file():
                try:
                    file_service.delete_file(file_path)
                except Exception:
                    pass  # Ignore cleanup errors
            
            return response
            
        except Exception as e:
            return ErrorHandler.handle_file_generation_error(format_type, str(e))
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


# Additional utility endpoints
@llm_bp.route('/profiles/<profile_id>', methods=['GET'])
def get_profile_details(profile_id: str):
    """GET /llm/profiles/{id} - Get details for a specific profile"""
    try:
        require_profile_id(profile_id)
        
        profile_dict = profile_service.get_profile_dict(profile_id)
        if not profile_dict:
            return ErrorHandler.handle_profile_not_found(profile_id)
        
        return jsonify(profile_dict), 200
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/profiles/<profile_id>/sample', methods=['GET'])
def get_profile_sample(profile_id: str):
    """GET /llm/profiles/{id}/sample - Get sample prompt for a profile"""
    try:
        require_profile_id(profile_id)
        
        if not profile_service.validate_profile_exists(profile_id):
            return ErrorHandler.handle_profile_not_found(profile_id)
        
        sample = prompt_service.create_sample_prompt(profile_id)
        return jsonify(sample), 200
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/timeout/calculate', methods=['POST'])
def calculate_timeout():
    """POST /llm/timeout/calculate - Calculate timeout for text and profile"""
    try:
        data = RequestValidator.validate_json_request(request)
        
        text = data.get('text', '')
        profile_id = data.get('profile_id')
        
        if text:
            require_text(text)
        if profile_id:
            require_profile_id(profile_id)
        
        text_length = len(text) if text else data.get('text_length', 0)
        timeout = get_timeout_for_text(text, profile_id, config) if text else 30
        
        from src.utils.timeout import get_timeout_calculator
        calculator = get_timeout_calculator(config)
        breakdown = calculator.get_timeout_breakdown(text_length, profile_id)
        estimate = calculator.estimate_processing_time(text_length, profile_id)
        
        return jsonify({
            "text_length": text_length,
            "profile_id": profile_id,
            "timeout": timeout,
            "breakdown": breakdown,
            "estimate": estimate
        }), 200
        
    except ValidationError as e:
        return ErrorHandler.handle_validation_error(e)
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


@llm_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """GET /llm/statistics - Get processing statistics"""
    try:
        result_stats = result_manager.get_statistics()
        history_stats = history_manager.get_global_statistics()
        profile_stats = profile_service.get_profile_statistics()
        
        return jsonify({
            "results": result_stats,
            "histories": history_stats,
            "profiles": profile_stats,
            "service_info": {
                "provider": config.LLM_PROVIDER,
                "model": config.OPENAI_MODEL,
                "base_url": config.LLM_BASE_URL
            }
        }), 200
        
    except Exception as e:
        return ErrorHandler.handle_internal_error(str(e))


# Error handlers for the blueprint
@llm_bp.errorhandler(404)
def not_found(error):
    return ErrorHandler.create_error_response(
        code="NOT_FOUND",
        message="Endpoint not found",
        status_code=404
    )


@llm_bp.errorhandler(405)
def method_not_allowed(error):
    return ErrorHandler.create_error_response(
        code="METHOD_NOT_ALLOWED",
        message="Method not allowed for this endpoint",
        status_code=405
    )


@llm_bp.errorhandler(500)
def internal_error(error):
    return ErrorHandler.handle_internal_error()
