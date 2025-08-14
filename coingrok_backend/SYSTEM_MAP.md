CoinGrok Backend – Ground‑Truth System Map 

⸻

1. End‑to‑End Request Flow (Mermaid)

flowchart TD
    Client[HTTP Request] --> FastAPI[FastAPI Application]
    FastAPI --> MW1[middleware/cors.py]
    MW1 --> MW2[middleware/security_headers.py]
    MW2 --> MW3[middleware/correlation_id.py]
    MW3 --> MW4[middleware/request_limits.py]
    MW4 --> MW5[middleware/error_handler.py]
    MW5 --> MW6[middleware/auth.py]
    MW6 --> Route[api/routes/analysis.py]

    Route --> DepRateLimit[api/dependencies_rate_limit.py]
    Route --> UserService[services/user_service.py]
    Route --> AnalysisService[services/analysis_service.py]

    AnalysisService --> OpenAIService[services/openai_service.py]
    AnalysisService --> GrokService[services/grok_service.py]

    OpenAIService --> HTTPUtil[utils/http.py]
    GrokService --> HTTPUtil
    HTTPUtil --> OpenAI[OpenAI API]
    HTTPUtil --> Grok[Grok API]

    Route --> BackgroundTasks[utils/background_tasks.py]
    UserService --> Database[(Database)]
    AnalysisService --> Database
    BackgroundTasks --> Database

    Note1[Order per middleware setup at app init - not derived here]


⸻

2. Component Dependency Graph (Mermaid)

flowchart TD
    %% API Routes
    analysis[api/routes/analysis.py] --> logging[app/core/logging.py]
    analysis --> dependencies[app/api/dependencies.py]
    analysis --> auth[app/middleware/auth.py]
    analysis --> rateLimit[app/api/dependencies_rate_limit.py]
    analysis --> schemas[app/models/schemas.py]
    analysis --> analysisService[app/services/analysis_service.py]
    analysis --> userService[app/services/user_service.py]
    analysis --> backgroundTasks[app/utils/background_tasks.py]
    analysis --> exceptions[app/core/exceptions.py]
    analysis --> database[app/models/database.py]

    health[api/routes/health.py] --> logging
    health --> config[app/core/config.py]
    health --> schemas
    health --> dependencies

    jobs[api/routes/jobs.py] --> logging
    jobs --> dependencies
    jobs --> database

    queryLogs[api/routes/query_logs.py] --> logging
    queryLogs --> dependencies
    queryLogs --> database
    queryLogs --> schemas

    users[api/routes/users.py] --> logging
    users --> dependencies
    users --> auth
    users --> userService
    users --> schemas

    %% Middleware
    auth --> config
    auth --> logging
    cors[middleware/cors.py] --> config
    cors --> logging
    errorHandler[middleware/error_handler.py] --> logging
    errorHandler --> exceptions
    requestLimits[middleware/request_limits.py] --> config
    requestLimits --> logging
    securityHeaders[middleware/security_headers.py] --> config
    correlationId[middleware/correlation_id.py] --> logging

    %% Services
    analysisService --> logging
    analysisService --> database
    analysisService --> openaiService[app/services/openai_service.py]
    analysisService --> grokService[app/services/grok_service.py]
    analysisService --> exceptions

    openaiService --> config
    openaiService --> logging
    openaiService --> exceptions
    openaiService --> ashPrompt[app/ash_prompt.py]
    openaiService --> httpUtil[app/utils/http.py]

    grokService --> config
    grokService --> logging
    grokService --> exceptions
    grokService --> httpUtil

    userService --> database
    userService --> logging

    %% Utilities
    httpUtil --> config
    httpUtil --> logging

    backgroundTasks --> logging
    backgroundTasks --> dbEngine[app/database.py]
    backgroundTasks --> database
    backgroundTasks --> enums[app/models/enums.py]
    backgroundTasks --> analysisService

    rateLimitUtil[utils/rate_limit.py] --> config
    rateLimitUtil --> logging

    %% Core/Models
    database --> enums
    schemas --> config
    dbEngine --> config
    dbEngine --> logging
    dbEngine --> database
    logging --> config
    logging --> correlationId


⸻

3. Entity Relationship Diagram (Mermaid)

erDiagram
    User {
        int id PK
        string email
        datetime created_at
        string subscription_tier
        int queries_used
        int queries_limit
        string google_id
        bool is_active
    }

    AnalysisJob {
        int id PK
        string job_id
        string user_input
        JobStatus status
        datetime created_at
        datetime completed_at
        string optimized_prompt
        string analysis
        string error
        string user_id FK
        float cost
    }

    QueryLog {
        int id PK
        string user_id FK
        string user_input
        string optimized_prompt
        string ai_result
        datetime created_at
        int response_time_ms
        bool success
        string error_message
        float openai_cost
        float grok_cost
        float total_cost
    }

    JobStatus {
        string QUEUED
        string PROCESSING_OPENAI
        string PROCESSING_GROK
        string COMPLETED
        string FAILED
    }

    User ||--o{ AnalysisJob : "user_id"
    User ||--o{ QueryLog : "user_id"
    AnalysisJob ||--|| JobStatus : "status"


⸻

4. Data Flow Summary for /analysis

The /analysis endpoint in api/routes/analysis.py orchestrates a multi-step flow:
	1.	Calls app/middleware/auth.py for authentication.
	2.	Checks limits via app/api/dependencies_rate_limit.py.
	3.	Invokes app/services/user_service.py to validate query limits in app/models/database.py.
	4.	Routes to app/services/analysis_service.py, which calls app/services/openai_service.py and app/services/grok_service.py.
	5.	Both AI services use app/utils/http.py for resilient requests to OpenAI and Grok APIs.
	6.	Configuration is pulled from app/core/config.py; errors use app/core/exceptions.py.
	7.	Logging is centralized via app/core/logging.py.
	8.	For async runs, app/utils/background_tasks.py manages jobs, persisting status through app/models/enums.py and app/models/database.py.