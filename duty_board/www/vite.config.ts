import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';
import react from "@vitejs/plugin-react-swc";
import viteTsconfigPaths from 'vite-tsconfig-paths';
import htmlPurge from 'vite-plugin-html-purgecss';
import { createHtmlPlugin } from 'vite-plugin-html';
import viteCompression from 'vite-plugin-compression';



export default defineConfig({
    // depending on your application, base can also be "/"
    base: '',
    build: {
        cssCodeSplit: false,
        cssMinify: true
    },
    plugins: [
        react(),
        viteTsconfigPaths(),
        // htmlPurge(),
        createHtmlPlugin({
          entry: 'js/index.tsx',
          template: 'index.html',
        }),
        viteCompression()
    ],
    server: {
        // this ensures that the browser opens upon server start
        open: true,
        // this sets a default port to 3000
        port: 8080,
    },

})