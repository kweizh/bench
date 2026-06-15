"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CorrelationHook = void 0;
class CorrelationHook {
    async afterError(_hookCtx, response, error) {
        if (response !== null &&
            response.status === 500 &&
            response.headers.has("x-correlation-id")) {
            const correlationId = response.headers.get("x-correlation-id");
            throw new Error(`Correlation Error: ${correlationId}`);
        }
        return { response, error };
    }
}
exports.CorrelationHook = CorrelationHook;
