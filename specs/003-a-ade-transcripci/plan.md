
# Implementation Plan: Transcripción en Streaming (Tiempo Real)

**Branch**: `003-a-ade-transcripci` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-a-ade-transcripci/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implementar transcripción en streaming en tiempo real para AudioLetra usando WebSockets con Flask-SocketIO, captura de audio con MediaRecorder, y procesamiento incremental con faster-whisper local. La funcionalidad debe ser visible y funcional en el frontend actual con nueva vista "Streaming".

## Technical Context
**Language/Version**: Python 3.11+, JavaScript ES6+  
**Primary Dependencies**: Flask-SocketIO, faster-whisper, MediaRecorder API, WebSocket  
**Storage**: Archivos de transcripción locales (mismo formato existente)  
**Testing**: pytest, JavaScript testing framework  
**Target Platform**: Navegadores Chrome/Edge, servidor Flask local  
**Project Type**: web (Flask backend + HTML/JS frontend)  
**Performance Goals**: Latencia <2s para primera transcripción, <3s umbral de advertencia  
**Constraints**: 8GB RAM mínimo, 60min límite de sesión, privacidad local (no audio externo)  
**Scale/Scope**: Sesiones concurrentes múltiples, reconexión automática, fallback a modo por bloques

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Privacidad ✅
- ✅ Audio procesado completamente en local con faster-whisper
- ✅ No envío de audio a servicios externos
- ✅ Solo texto puede enviarse a LLM (opcional)
- ✅ Audio eliminado inmediatamente después de transcripción

### Simplicidad ✅
- ✅ Interfaz intuitiva con máximo 3 clics para acciones principales
- ✅ Tiempo de respuesta <2s para transcripción inicial
- ✅ Funciones críticas sin configuración previa

### Tecnología ✅
- ✅ Python 3.11+ con Flask
- ✅ WebSockets para tiempo real (Flask-SocketIO)
- ✅ faster-whisper local con soporte GPU
- ✅ HTML/JS ligero sin frameworks pesados

### Seguridad y Calidad ✅
- ✅ Eliminación automática de audio tras transcripción
- ✅ Validación de archivos y tamaños
- ✅ Logs sin datos sensibles
- ✅ Código siguiendo PEP8

**Status**: ✅ PASS - Diseño cumple todos los principios constitucionales

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application) - AudioLetra es una aplicación web con backend Flask y frontend HTML/JS integrado

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType cursor`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Specific Tasks for Streaming Feature**:
1. **Backend Infrastructure**:
   - Flask-SocketIO setup y configuración
   - WebSocket event handlers
   - Cola asíncrona de procesamiento
   - Modelos de datos (StreamingSession, AudioChunk, TranscriptionResult)

2. **Frontend Components**:
   - Nueva plantilla stream.html
   - JavaScript para MediaRecorder API
   - WebSocket client implementation
   - UI states y controles

3. **Audio Processing**:
   - faster-whisper integration
   - Chunk processing pipeline
   - Resultado parcial vs final
   - Métricas de rendimiento

4. **Testing**:
   - Contract tests para WebSocket events
   - Integration tests para flujo completo
   - Performance tests para latencia
   - UI tests para estados y controles

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
