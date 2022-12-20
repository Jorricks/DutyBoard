const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const { DefinePlugin } = require("webpack");
const path = require("path");
const CompressionPlugin = require("compression-webpack-plugin");


module.exports = merge(common, {
  mode: 'production',
  devtool: 'source-map',
  output: {
    path: path.resolve(__dirname, "dist"), // output folder
    publicPath: "/dist/"
  },
  plugins: [
      new DefinePlugin({
        'process.env.API_ADDRESS': JSON.stringify("/"),
        'process.env.PRODUCTION': JSON.stringify(true),
      }),
      new CompressionPlugin({
        compressionOptions: { level: 9 },
      })
  ],
});
