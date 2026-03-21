/**
 * Shared Winston logger for the Pelota API.
 * Console transport with timestamp and level.
 */

import winston from "winston";

export const logger = winston.createLogger({
  level: process.env.PELOTA_LOG_LEVEL ?? "info",
  format: winston.format.combine(
    winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
    winston.format.errors({ stack: true }),
    winston.format.printf(({ level, message, timestamp, ...meta }) => {
      const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : "";
      return `${timestamp} [${level}] ${message}${metaStr}`;
    })
  ),
  transports: [new winston.transports.Console()],
});
