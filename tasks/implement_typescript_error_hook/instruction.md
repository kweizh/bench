# Implement Custom TypeScript Error Hook

## Background
Speakeasy allows customizing SDK behavior using "hooks". You need to implement a custom TypeScript error hook that intercepts API errors and extracts a custom `x-correlation-id` header from the response, throwing a custom error with this ID.

## Requirements
- You have a Speakeasy SDK hooks directory at `/home/user/sdk/src/hooks`.
- Create a custom hook `src/hooks/custom/correlation.ts` that implements `AfterErrorHook`.
- In `afterError`, if the `response` is not null, has a status code of 500, and contains the header `x-correlation-id`, the hook should throw a new standard `Error` with the exact message: `Correlation Error: <correlation_id>` (replace `<correlation_id>` with the actual header value).
- If the condition is not met, the hook must return the original `response` and `error` unchanged as `{ response, error }`.
- Register the hook in `src/hooks/registration.ts` by calling `hooks.registerAfterErrorHook(new CorrelationHook())`.

## Implementation Guide
1. Navigate to `/home/user/sdk`.
2. Create `src/hooks/custom/correlation.ts`.
3. Implement the `CorrelationHook` class using the `AfterErrorHook` and `AfterErrorContext` interfaces from `../types.js`.
4. Update `src/hooks/registration.ts` to import and register your hook in `initHooks(hooks: Hooks)`.
5. Run `npx tsc --noEmit` in the `sdk` directory to ensure there are no TypeScript errors.

## Constraints
- Project path: /home/user/sdk
- Do not modify `src/hooks/types.ts`.
- Ensure you export `CorrelationHook` from `correlation.ts`.