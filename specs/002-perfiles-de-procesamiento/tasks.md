# Tasks: Perfiles de Procesamiento con LLM

**Input**: Design documents from `/specs/002-perfiles-de-procesamiento/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `backend/src/`, `frontend/src/` per plan.md structure

## Phase 3.1: Setup
- [x] T001 Create backend/src structure per implementation plan
- [x] T002 Initialize Python project with Flask dependencies (python-docx, reportlab, jinja2)
- [x] T003 [P] Configure linting and formatting tools (flake8, black)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test POST /llm/process in backend/tests/contract/test_llm_process.py
- [x] T005 [P] Contract test GET /llm/profiles in backend/tests/contract/test_llm_profiles.py
- [x] T006 [P] Contract test GET /llm/results/{id} in backend/tests/contract/test_llm_results.py
- [x] T007 [P] Contract test POST /llm/download/{id} in backend/tests/contract/test_llm_download.py
- [x] T008 [P] Integration test profile processing flow in backend/tests/integration/test_profile_processing.py
- [x] T009 [P] Integration test multiple profiles same text in backend/tests/integration/test_multiple_profiles.py
- [x] T010 [P] Integration test error handling in backend/tests/integration/test_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T011 [P] Profile model in backend/src/models/profile.py
- [x] T012 [P] ProcessingResult model in backend/src/models/result.py
- [x] T013 [P] ResultHistory model in backend/src/models/history.py
- [x] T014 [P] LLM service abstraction in backend/src/services/llm_service.py
- [x] T015 [P] Profile service in backend/src/services/profile_service.py
- [x] T016 [P] Prompt template manager in backend/src/services/prompt_service.py
- [x] T017 [P] File generation service in backend/src/services/file_service.py
- [x] T018 POST /llm/process endpoint in backend/src/api/llm_routes.py
- [x] T019 GET /llm/profiles endpoint in backend/src/api/llm_routes.py
- [x] T020 GET /llm/results/{id} endpoint in backend/src/api/llm_routes.py
- [x] T021 POST /llm/download/{id} endpoint in backend/src/api/llm_routes.py
- [x] T022 [P] Input validation and error handling in backend/src/utils/validation.py
- [x] T023 [P] Timeout calculation logic in backend/src/utils/timeout.py

## Phase 3.4: Integration
- [x] T024 Connect LLM service to OpenAI/OpenRouter APIs
- [x] T025 Flask Blueprint registration
- [x] T026 Request/response logging
- [x] T027 Error response formatting
- [x] T028 Frontend profile dropdown integration
- [x] T029 Frontend result panel implementation
- [x] T030 Frontend state management for multiple results
- [x] T031 [P] Audio cleanup integration in backend/src/services/audio_cleanup.py

## Phase 3.5: Polish
- [x] T032 [P] Unit tests for models in backend/tests/unit/test_models.py
- [x] T033 [P] Unit tests for services in backend/tests/unit/test_services.py
- [x] T034 [P] Unit tests for validation in backend/tests/unit/test_validation.py
- [x] T035 Performance tests (timeout calculation)
- [x] T036 [P] Update docs/prompts.md with actual template files
- [x] T037 Remove duplication and optimize
- [x] T038 Run quickstart.md validation scenarios

## Dependencies
- Tests (T004-T010) before implementation (T011-T023)
- T011-T013 blocks T014-T017
- T014-T017 blocks T018-T021
- T018-T021 blocks T024-T030
- T031 can run in parallel with T024-T030
- Implementation before polish (T032-T038)

## Parallel Example
```
# Launch T004-T010 together:
Task: "Contract test POST /llm/process in backend/tests/contract/test_llm_process.py"
Task: "Contract test GET /llm/profiles in backend/tests/contract/test_llm_profiles.py"
Task: "Contract test GET /llm/results/{id} in backend/tests/contract/test_llm_results.py"
Task: "Contract test POST /llm/download/{id} in backend/tests/contract/test_llm_download.py"
Task: "Integration test profile processing flow in backend/tests/integration/test_profile_processing.py"
Task: "Integration test multiple profiles same text in backend/tests/integration/test_multiple_profiles.py"
Task: "Integration test error handling in backend/tests/integration/test_error_handling.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Follow constitutional principles (privacy, simplicity, security)

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
