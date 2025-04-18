from fastapi import FastAPI, HTTPException
from app.scraper import (
    scrape,
    scrape_batch,
    SingleScrapeRequest,
    BatchScrapeRequest,
    ScrapeResponse,
    BatchScrapeResponse,
)

app = FastAPI(
    title="Apollo WebSpider",
    description="A microservice for scraping web content",
    version="0.1.0",
)


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(request: SingleScrapeRequest) -> ScrapeResponse:

    return await scrape(request.url)


@app.post("/scrape/batch", response_model=BatchScrapeResponse)
async def scrape_batch_endpoint(request: BatchScrapeRequest) -> BatchScrapeResponse:

    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    return await scrape_batch(request.urls)


@app.get("/")
async def root():
    return {"status": "ok", "service": "Apollo WebSpider"}
