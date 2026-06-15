/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // Re-export the server-side ZEALT_RUN_ID so the browser bundle can access it
    NEXT_PUBLIC_ZEALT_RUN_ID: process.env.ZEALT_RUN_ID,
  },
};
module.exports = nextConfig;
