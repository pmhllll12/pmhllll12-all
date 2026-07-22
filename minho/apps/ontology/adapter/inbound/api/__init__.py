from fastapi import APIRouter
from ontology.adapter.inbound.api.v1.crawler_router import crawl_router
from ontology.adapter.inbound.api.v1.face_recognition_router import face_recognition_router
from ontology.adapter.inbound.api.v1.gemini_router import gemini_router
from ontology.adapter.inbound.api.v1.image_classifier_router import image_classifier_router
from ontology.adapter.inbound.api.v1.scraper_router import scrape_router
from ontology.adapter.inbound.api.v1.semantic_router import semantic_router
from ontology.adapter.inbound.api.v1.vision_router import image_analysis_router

vision_router = APIRouter(prefix="/api/vision")
vision_router.include_router(image_analysis_router)
vision_router.include_router(face_recognition_router)
vision_router.include_router(image_classifier_router)

crawler_router = APIRouter(prefix="/api/ontology")
crawler_router.include_router(crawl_router)
crawler_router.include_router(scrape_router)

ontology_router = APIRouter(prefix="/api/ontology")
ontology_router.include_router(gemini_router)
ontology_router.include_router(semantic_router)
