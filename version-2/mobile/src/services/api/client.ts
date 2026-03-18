/**
 * Typed API client for all TouchMap backend endpoints.
 * Every method maps to a single REST endpoint with typed request/response.
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import { API_BASE_URL } from "../../constants/config";
import type {
  ScanResponse,
  ScanDetailResponse,
  TaskPlanResponse,
  TaskRepeatResponse,
  TaskClarifyResponse,
  LocateResponse,
  ExploreResponse,
  GuidanceStartResponse,
  GuidanceFrameResponse,
  GuidanceStopResponse,
} from "../../models/api";

class TouchMapApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: { "Content-Type": "application/json" },
    });
  }

  // --- Scan pipeline ---

  async scanPanel(imageFormData: FormData): Promise<ScanResponse> {
    const response = await this.client.post<ScanResponse>("/scan", imageFormData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 60000,
    });
    return response.data;
  }

  async getScan(scanId: string): Promise<ScanDetailResponse> {
    const response = await this.client.get<ScanDetailResponse>(`/scan/${scanId}`);
    return response.data;
  }

  // --- Task mode ---

  async planTask(scanId: string, userRequest: string): Promise<TaskPlanResponse> {
    const response = await this.client.post<TaskPlanResponse>("/task/plan", {
      scan_id: scanId,
      user_request: userRequest,
    });
    return response.data;
  }

  async repeatTaskStep(
    scanId: string,
    taskId: string,
    currentStep: number
  ): Promise<TaskRepeatResponse> {
    const response = await this.client.post<TaskRepeatResponse>("/task/repeat", {
      scan_id: scanId,
      task_id: taskId,
      current_step: currentStep,
    });
    return response.data;
  }

  async clarifyTaskStep(
    scanId: string,
    taskId: string,
    currentStep: number,
    question: string
  ): Promise<TaskClarifyResponse> {
    const response = await this.client.post<TaskClarifyResponse>("/task/clarify", {
      scan_id: scanId,
      task_id: taskId,
      current_step: currentStep,
      question,
    });
    return response.data;
  }

  // --- Locate mode ---

  async locateControl(scanId: string, query: string): Promise<LocateResponse> {
    const response = await this.client.post<LocateResponse>("/locate", {
      scan_id: scanId,
      query,
    });
    return response.data;
  }

  // --- Explore mode ---

  async explorePanel(scanId: string, query: string): Promise<ExploreResponse> {
    const response = await this.client.post<ExploreResponse>("/explore", {
      scan_id: scanId,
      query,
    });
    return response.data;
  }

  // --- Live guidance ---

  async startGuidance(
    scanId: string,
    targetControlId: string
  ): Promise<GuidanceStartResponse> {
    const response = await this.client.post<GuidanceStartResponse>("/guidance/start", {
      scan_id: scanId,
      target_control_id: targetControlId,
    });
    return response.data;
  }

  async processGuidanceFrame(
    guidanceSessionId: string,
    frameFormData: FormData
  ): Promise<GuidanceFrameResponse> {
    frameFormData.append("guidance_session_id", guidanceSessionId);
    const response = await this.client.post<GuidanceFrameResponse>(
      "/guidance/frame",
      frameFormData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return response.data;
  }

  async stopGuidance(guidanceSessionId: string): Promise<GuidanceStopResponse> {
    const response = await this.client.post<GuidanceStopResponse>("/guidance/stop", {
      guidance_session_id: guidanceSessionId,
    });
    return response.data;
  }

  // --- Health ---

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }
}

export const apiClient = new TouchMapApiClient();
export default TouchMapApiClient;
