import { AfterErrorContext, AfterErrorHook } from "../types.js";

export class CorrelationHook implements AfterErrorHook {
  afterError(
    _hookCtx: AfterErrorContext,
    response: Response | null,
    error: unknown,
  ) {
    if (response && response.status === 500) {
      const correlationId = response.headers.get("x-correlation-id");
      if (correlationId) {
        throw new Error(`Correlation Error: ${correlationId}`);
      }
    }

    return { response, error };
  }
}
