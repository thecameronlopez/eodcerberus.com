import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const SERVER = process.env.SERVER_URL;

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [
      react({
        babel: {
          plugins: [["babel-plugin-react-compiler"]],
        },
      }),
    ],
    server: {
      proxy: {
        "/api": {
          target: env.SERVER_URL,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
