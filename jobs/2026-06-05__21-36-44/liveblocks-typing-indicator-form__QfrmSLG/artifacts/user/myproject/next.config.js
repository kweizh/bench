/** @type {import('next').NextConfig} */
const runId = process.env.ZEALT_RUN_ID;
const roomId = runId ? `harbor-typing-form-${runId}` : "harbor-typing-form-local";

const nextConfig = {
  reactStrictMode: false,
  env: {
    NEXT_PUBLIC_ROOM_ID: roomId,
  },
};
module.exports = nextConfig;
