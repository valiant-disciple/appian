/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      'monaco-editor': '@monaco-editor/react'
    }
    return config
  }
}

module.exports = nextConfig 