const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const { DefinePlugin } = require("webpack");
const path = require("path");

module.exports = merge(common, {
  mode: 'development',
  devtool: 'eval-cheap-source-map',
  output: {
    path: path.resolve(__dirname, "dist"), // output folder
    publicPath: "/"  // This is required, otherwise double linking in URLs won't work ;'(
  },
  plugins: [
      new DefinePlugin({
        'process.env.API_ADDRESS': JSON.stringify("http://127.0.0.1:8000/"),
        'process.env.PRODUCTION': JSON.stringify(false),
      })
  ],
});
