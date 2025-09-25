"""
Audio cleanup service integration
Handles automatic cleanup of audio files after transcription
"""
import os
import time
import logging
from typing import List, Optional
from pathlib import Path
from src.config import Config


class AudioCleanupService:
    """Service for managing audio file cleanup"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger('audiLetra.audio_cleanup')
        self.cleanup_enabled = True
        self.cleanup_delay = 5  # seconds after transcription
        self.max_file_age = 3600  # 1 hour in seconds
        
    def schedule_cleanup(self, file_path: str, delay: Optional[int] = None) -> bool:
        """Schedule a file for cleanup after specified delay"""
        if not self.cleanup_enabled:
            return False
            
        if not os.path.exists(file_path):
            self.logger.warning(f"File does not exist for cleanup: {file_path}")
            return False
        
        delay = delay or self.cleanup_delay
        
        # In a real implementation, you might use a background task queue
        # For now, we'll use a simple approach with file timestamps
        try:
            # Create a cleanup marker file
            marker_path = f"{file_path}.cleanup"
            with open(marker_path, 'w') as f:
                f.write(str(time.time() + delay))
            
            self.logger.info(f"Scheduled cleanup for {file_path} in {delay}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule cleanup for {file_path}: {e}")
            return False
    
    def cleanup_scheduled_files(self) -> int:
        """Clean up files that are ready for deletion"""
        if not self.cleanup_enabled:
            return 0
            
        cleaned_count = 0
        
        try:
            # Find all cleanup marker files
            temp_dir = Path(self.config.UPLOAD_FOLDER)
            if not temp_dir.exists():
                return 0
                
            for marker_file in temp_dir.glob("*.cleanup"):
                try:
                    # Read cleanup time
                    with open(marker_file, 'r') as f:
                        cleanup_time = float(f.read().strip())
                    
                    # Check if it's time to clean up
                    if time.time() >= cleanup_time:
                        # Get the original file path
                        original_file = str(marker_file).replace('.cleanup', '')
                        
                        # Delete both files
                        if self._delete_file_safely(original_file):
                            cleaned_count += 1
                            self.logger.info(f"Cleaned up audio file: {original_file}")
                        
                        # Remove marker file
                        marker_file.unlink()
                        
                except Exception as e:
                    self.logger.error(f"Error processing cleanup marker {marker_file}: {e}")
                    # Remove corrupted marker file
                    try:
                        marker_file.unlink()
                    except:
                        pass
        
        except Exception as e:
            self.logger.error(f"Error during cleanup process: {e}")
        
        return cleaned_count
    
    def cleanup_old_files(self, max_age: Optional[int] = None) -> int:
        """Clean up files older than specified age"""
        max_age = max_age or self.max_file_age
        cleaned_count = 0
        
        try:
            temp_dir = Path(self.config.UPLOAD_FOLDER)
            if not temp_dir.exists():
                return 0
            
            current_time = time.time()
            
            # Find audio files
            audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    # Check if it's an audio file
                    if any(file_path.suffix.lower() in ext for ext in audio_extensions):
                        # Check file age
                        file_age = current_time - file_path.stat().st_mtime
                        
                        if file_age > max_age:
                            if self._delete_file_safely(str(file_path)):
                                cleaned_count += 1
                                self.logger.info(f"Cleaned up old audio file: {file_path}")
        
        except Exception as e:
            self.logger.error(f"Error during old file cleanup: {e}")
        
        return cleaned_count
    
    def cleanup_immediately(self, file_path: str) -> bool:
        """Clean up a file immediately"""
        if not os.path.exists(file_path):
            return True
        
        try:
            if self._delete_file_safely(file_path):
                self.logger.info(f"Immediately cleaned up audio file: {file_path}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to immediately clean up {file_path}: {e}")
        
        return False
    
    def cleanup_all_temp_files(self) -> int:
        """Clean up all temporary files in the upload directory"""
        cleaned_count = 0
        
        try:
            temp_dir = Path(self.config.UPLOAD_FOLDER)
            if not temp_dir.exists():
                return 0
            
            # Clean up audio files
            audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    # Check if it's an audio file or cleanup marker
                    if (any(file_path.suffix.lower() in ext for ext in audio_extensions) or 
                        file_path.name.endswith('.cleanup')):
                        
                        if self._delete_file_safely(str(file_path)):
                            cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} temporary files")
            
        except Exception as e:
            self.logger.error(f"Error during full cleanup: {e}")
        
        return cleaned_count
    
    def _delete_file_safely(self, file_path: str) -> bool:
        """Safely delete a file with error handling"""
        try:
            os.remove(file_path)
            return True
        except PermissionError:
            self.logger.warning(f"Permission denied when deleting {file_path}")
            return False
        except FileNotFoundError:
            # File already deleted
            return True
        except Exception as e:
            self.logger.error(f"Unexpected error deleting {file_path}: {e}")
            return False
    
    def get_cleanup_stats(self) -> dict:
        """Get statistics about cleanup operations"""
        try:
            temp_dir = Path(self.config.UPLOAD_FOLDER)
            if not temp_dir.exists():
                return {
                    'total_files': 0,
                    'audio_files': 0,
                    'cleanup_markers': 0,
                    'total_size': 0
                }
            
            total_files = 0
            audio_files = 0
            cleanup_markers = 0
            total_size = 0
            
            audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
                    
                    if file_path.name.endswith('.cleanup'):
                        cleanup_markers += 1
                    elif any(file_path.suffix.lower() in ext for ext in audio_extensions):
                        audio_files += 1
            
            return {
                'total_files': total_files,
                'audio_files': audio_files,
                'cleanup_markers': cleanup_markers,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cleanup stats: {e}")
            return {}
    
    def enable_cleanup(self):
        """Enable automatic cleanup"""
        self.cleanup_enabled = True
        self.logger.info("Audio cleanup enabled")
    
    def disable_cleanup(self):
        """Disable automatic cleanup"""
        self.cleanup_enabled = False
        self.logger.info("Audio cleanup disabled")
    
    def set_cleanup_delay(self, delay: int):
        """Set cleanup delay in seconds"""
        self.cleanup_delay = max(0, delay)
        self.logger.info(f"Cleanup delay set to {self.cleanup_delay}s")
    
    def set_max_file_age(self, max_age: int):
        """Set maximum file age in seconds"""
        self.max_file_age = max(0, max_age)
        self.logger.info(f"Max file age set to {self.max_file_age}s")


# Global service instance
_audio_cleanup_service: Optional[AudioCleanupService] = None


def get_audio_cleanup_service(config: Optional[Config] = None) -> AudioCleanupService:
    """Get or create the global audio cleanup service instance"""
    global _audio_cleanup_service
    
    if _audio_cleanup_service is None:
        _audio_cleanup_service = AudioCleanupService(config)
    
    return _audio_cleanup_service


def reset_audio_cleanup_service():
    """Reset the global audio cleanup service instance"""
    global _audio_cleanup_service
    _audio_cleanup_service = None


# Integration functions for existing AudioLetra code
def cleanup_after_transcription(audio_file_path: str, delay: int = 5):
    """Convenience function to cleanup audio after transcription"""
    service = get_audio_cleanup_service()
    return service.schedule_cleanup(audio_file_path, delay)


def cleanup_immediately(audio_file_path: str):
    """Convenience function to cleanup audio immediately"""
    service = get_audio_cleanup_service()
    return service.cleanup_immediately(audio_file_path)


def run_cleanup_maintenance():
    """Run cleanup maintenance (call this periodically)"""
    service = get_audio_cleanup_service()
    
    # Clean up scheduled files
    scheduled_count = service.cleanup_scheduled_files()
    
    # Clean up old files
    old_count = service.cleanup_old_files()
    
    return {
        'scheduled_cleaned': scheduled_count,
        'old_cleaned': old_count,
        'total_cleaned': scheduled_count + old_count
    }
