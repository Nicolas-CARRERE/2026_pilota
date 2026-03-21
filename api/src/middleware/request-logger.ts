/**
 * Request logging middleware.
 * Logs method, path, statusCode, and duration on response finish.
 */

import { Request, Response, NextFunction } from "express";
import { logger } from "../logger.js";

export function requestLogger(
  request: Request,
  response: Response,
  next: NextFunction
): void {
  const start = Date.now();
  response.on("finish", () => {
    const durationMs = Date.now() - start;
    logger.info("request", {
      method: request.method,
      path: request.path,
      statusCode: response.statusCode,
      durationMs,
    });
  });
  next();
}
