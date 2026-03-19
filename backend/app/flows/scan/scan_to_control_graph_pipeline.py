"""
Pipeline: image bytes → preprocess → OCR → panelmap extraction → validation → control graph → session store.

Single entry point run(); each step delegates to the injected service. The control graph is built from
the validated panel map to add row/column/region and spatial edges for locate/explore/guidance.
"""
from __future__ import annotations

from app.core.logging import logger
from app.domain.schemas.scan_schemas import ScanResponse
from app.services.graphs.control_graph_builder_service import ControlGraphService
from app.services.ocr.ocr_extraction_service import OCRService
from app.services.panelmap.panelmap_vision_extraction_service import PanelMapExtractionService
from app.services.panelmap.panelmap_normalization_service import PanelMapValidationService
from app.services.scans.image_preprocessing_service import PreprocessedResult, ScanProcessingService
from app.services.sessions.in_memory_session_store import SessionService


class ScanPipeline:
    def __init__(
        self,
        *,
        scan_processor: ScanProcessingService,
        ocr_service: OCRService,
        panelmap_extractor: PanelMapExtractionService,
        panelmap_validator: PanelMapValidationService,
        graph_service: ControlGraphService,
        session_service: SessionService,
    ):
        self._scan_processor = scan_processor
        self._ocr_service = ocr_service
        self._panelmap_extractor = panelmap_extractor
        self._panelmap_validator = panelmap_validator
        self._graph_service = graph_service
        self._session_service = session_service

    async def run(self, *, image_bytes: bytes, scan_id: str, session_id: str) -> ScanResponse:
        # Order: preprocess image → OCR tokens → extract panelmap (Vision) → validate/normalize → build graph → store
        preprocessed = await self._preprocess(image_bytes=image_bytes, scan_id=scan_id)
        ocr_result = await self._run_ocr(cleaned_image=preprocessed.cleaned_image)
        raw_panel_map = await self._extract_panelmap(
            cleaned_image=preprocessed.cleaned_image,
            ocr_tokens=ocr_result.tokens,
            scan_id=scan_id,
        )
        panel_map = await self._validate_panelmap(raw_panel_map)
        control_graph = self._build_control_graph(panel_map)
        await self._store_scan(
            scan_id=scan_id,
            session_id=session_id,
            panel_map=panel_map,
            control_graph=control_graph,
            ocr_result=ocr_result,
            preprocessed_image_ref=preprocessed.image_ref,
        )

        return ScanResponse(
            scan_id=scan_id,
            session_id=session_id,
            preprocessed_image_ref=preprocessed.image_ref,
            ocr_result=ocr_result,
            panel_map=panel_map,
            control_graph_summary={
                "node_count": len(control_graph.nodes),
                "edge_count": len(control_graph.edges),
                "region_count": len(control_graph.regions),
            },
            confidence=panel_map.scan_confidence,
        )

    async def _preprocess(self, *, image_bytes: bytes, scan_id: str) -> PreprocessedResult:
        logger.info(f"Preprocessing scan image: scan_id={scan_id}")
        return await self._scan_processor.process(image_bytes, scan_id)

    async def _run_ocr(self, *, cleaned_image) -> object:
        # Keep typing light here; the OCR service returns `OCRResult` from `app.domain.schemas.scan_schemas`.
        logger.info("Running OCR extraction")
        return await self._ocr_service.extract(cleaned_image)

    async def _extract_panelmap(self, *, cleaned_image, ocr_tokens, scan_id: str):
        return await self._panelmap_extractor.extract(
            cleaned_image=cleaned_image,
            ocr_tokens=ocr_tokens,
            scan_id=scan_id,
        )

    async def _validate_panelmap(self, raw_panel_map):
        return await self._panelmap_validator.validate_and_normalize(raw_panel_map)

    def _build_control_graph(self, panel_map):
        # Builds spatial graph (rows, columns, regions, edges) for locate/explore/guidance
        return self._graph_service.build(panel_map)

    async def _store_scan(
        self,
        *,
        scan_id: str,
        session_id: str,
        panel_map,
        control_graph,
        ocr_result,
        preprocessed_image_ref: str,
    ):
        await self._session_service.store_scan(
            scan_id=scan_id,
            session_id=session_id,
            panel_map=panel_map,
            control_graph=control_graph,
            ocr_result=ocr_result,
            preprocessed_image_ref=preprocessed_image_ref,
        )

