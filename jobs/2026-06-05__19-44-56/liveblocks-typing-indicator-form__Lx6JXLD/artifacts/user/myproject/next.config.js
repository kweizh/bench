/** @type {import('next').NextConfig} */
const nextConfig = { 
  reactStrictMode: false,
  env: {
    ZEALT_RUN_ID: process.env.ZEALT_RUN_ID,
  }
};
module.exports = nextConfig;
