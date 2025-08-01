import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import user, system
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, GROK_API_KEY
from app.ash_prompt import ASH_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CoinGrok Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize API clients with error handling
try:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    xai_client = AsyncClient(api_key=GROK_API_KEY)
    logger.info("API clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize API clients: {str(e)}")
    raise

class AnalysisRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=5000)

    @validator("user_input")
    def validate_user_input(cls, v: str) -> str:
        """Ensure user input is not empty or whitespace."""
        if not v.strip():
            raise ValueError("User input cannot be empty or whitespace only")
        return v.strip()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    """Analyze user input using OpenAI and Grok"""
    logger.info(f"Starting analysis for input length: {len(req.user_input)}")

    try:
        # === Step 1: Get optimized prompt from OpenAI ===
        logger.info("Requesting prompt optimization from OpenAI")

        ash_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ASH_SYSTEM_PROMPT},
                {"role": "user", "content": req.user_input},
            ],
        )

        # Validate OpenAI response
        if not ash_response.choices or not ash_response.choices[0].message.content:
            logger.error("Empty or invalid response from OpenAI")
            raise HTTPException(
                status_code=502, detail="Failed to get response from OpenAI"
            )

        optimized_prompt = ash_response.choices[0].message.content.strip()
        logger.info("Successfully received optimized prompt from OpenAI")

        # === Step 2: Send optimized prompt to Grok ===
        logger.info("Sending optimized prompt to Grok")

        chat = xai_client.chat.create(model="grok-4-latest")
        chat.append(system("You are an AI crypto analyst."))
        chat.append(user(optimized_prompt))
        response = await chat.sample()

        # Validate Grok response
        if not hasattr(response, "content") or not response.content:
            logger.error("Empty or invalid response from Grok")
            raise HTTPException(
                status_code=502, detail="Failed to get response from Grok"
            )

        final_answer = response.content
        logger.info("Successfully received analysis from Grok")

        return {
            "optimized_prompt": optimized_prompt,
            "analysis": final_answer,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed with error: {str(e)}")

        if "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
            )
        elif "api key" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="API authentication failed"
            )
        elif "timeout" in str(e).lower():
            raise HTTPException(
                status_code=504,
                detail="Request timeout. Please try again.",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Analysis failed due to internal error",
            )
