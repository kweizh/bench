import { AfterErrorContext, AfterErrorHook } from "../types.js";

export class CorrelationHook implements AfterErrorHook {
  async afterError(
    _hookCtx: AfterErrorContext,
    response: Response | null,
    error: unknown,
  ): Promise<{ response: Response | null; error: unknown }> {
    if (
      response !== null &&
      response.status === 500 &&
      response.headers.has("x-correlation-id")
    ) {
      const correlationId = response.headers.get("x-correlation-id");
      throw new Error(`Correlation Error: ${correlationId}`);
    }

    return { response, error };
  }
}
