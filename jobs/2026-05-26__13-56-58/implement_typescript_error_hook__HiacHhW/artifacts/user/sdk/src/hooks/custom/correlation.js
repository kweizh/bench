"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CorrelationHook = void 0;
class CorrelationHook {
    afterError(_hookCtx, response, error) {
        if (response && response.status === 500) {
            const correlationId = response.headers.get("x-correlation-id");
            if (correlationId) {
                throw new Error(`Correlation Error: ${correlationId}`);
            }
        }
        return { response, error };
    }
}
exports.CorrelationHook = CorrelationHook;
