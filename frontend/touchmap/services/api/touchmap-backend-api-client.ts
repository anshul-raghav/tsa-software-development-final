/**
 * Typed API client for all TouchMap backend endpoints.
 * Every method maps to a single REST endpoint with typed request/response.
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import { API_BASE_URL } from "../../constants/app-and-api-config";
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
} from "../../models/touchmap-backend-api-types";

/** Turns Axios or unknown errors into a single Error with a user-facing message for the UI. */
function normalizeApiError(error: unknown): Error {
  if (typeof __DEV__ !== "undefined" && __DEV__) {
    console.warn("API error", error);
  }
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    const status = axiosError.response?.status;
    const serverMessage =
      axiosError.response?.data?.detail ??
      axiosError.response?.data?.message ??
      axiosError.response?.data?.error;
    const baseMessage =
      typeof serverMessage === "string" && serverMessage.trim()
        ? serverMessage.trim()
        : axiosError.message || "Network request failed";

    const message =
      typeof status === "number" ? `Request failed (${status}): ${baseMessage}` : baseMessage;
    return new Error(message);
  }

  if (error instanceof Error) return error;
  return new Error(typeof error === "string" ? error : "Unexpected error");
}

class TouchMapApiClient {
  private httpClient: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.httpClient = axios.create({
      baseURL,
      timeout: 30000,
      headers: { "Content-Type": "application/json" },
    });
  }

  // --- Scan pipeline ---

  async scanPanel(imageFormData: FormData): Promise<ScanResponse> {
    try {
      const response = await this.httpClient.post<ScanResponse>("/scan", imageFormData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  async getScan(scanId: string): Promise<ScanDetailResponse> {
    try {
      const response = await this.httpClient.get<ScanDetailResponse>(`/scan/${scanId}`);
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  // --- Task mode ---

  async planTask(scanId: string, userRequest: string): Promise<TaskPlanResponse> {
    try {
      const response = await this.httpClient.post<TaskPlanResponse>("/task/plan", {
        scan_id: scanId,
        user_request: userRequest,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  async repeatTaskStep(
    scanId: string,
    taskId: string,
    currentStep: number
  ): Promise<TaskRepeatResponse> {
    try {
      const response = await this.httpClient.post<TaskRepeatResponse>("/task/repeat", {
        scan_id: scanId,
        task_id: taskId,
        current_step: currentStep,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  async clarifyTaskStep(
    scanId: string,
    taskId: string,
    currentStep: number,
    question: string
  ): Promise<TaskClarifyResponse> {
    try {
      const response = await this.httpClient.post<TaskClarifyResponse>("/task/clarify", {
        scan_id: scanId,
        task_id: taskId,
        current_step: currentStep,
        question,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  // --- Locate mode ---

  async locateControl(scanId: string, query: string): Promise<LocateResponse> {
    try {
      const response = await this.httpClient.post<LocateResponse>("/locate", {
        scan_id: scanId,
        query,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  // --- Explore mode ---

  async explorePanel(scanId: string, query: string): Promise<ExploreResponse> {
    try {
      const response = await this.httpClient.post<ExploreResponse>("/explore", {
        scan_id: scanId,
        query,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  // --- Live guidance ---

  async startGuidance(
    scanId: string,
    targetControlId: string
  ): Promise<GuidanceStartResponse> {
    try {
      const response = await this.httpClient.post<GuidanceStartResponse>("/guidance/start", {
        scan_id: scanId,
        target_control_id: targetControlId,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  async processGuidanceFrame(
    guidanceSessionId: string,
    frameFormData: FormData
  ): Promise<GuidanceFrameResponse> {
    frameFormData.append("guidance_session_id", guidanceSessionId);
    try {
      const response = await this.httpClient.post<GuidanceFrameResponse>(
        "/guidance/frame",
        frameFormData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  async stopGuidance(guidanceSessionId: string): Promise<GuidanceStopResponse> {
    try {
      const response = await this.httpClient.post<GuidanceStopResponse>("/guidance/stop", {
        guidance_session_id: guidanceSessionId,
      });
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }

  // --- Health ---

  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.httpClient.get("/health");
      return response.data;
    } catch (error) {
      throw normalizeApiError(error);
    }
  }
}

export const apiClient = new TouchMapApiClient();
export default TouchMapApiClient;
