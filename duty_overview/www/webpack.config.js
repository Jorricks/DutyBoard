const path = require("path");
const { WebpackManifestPlugin } = require("webpack-manifest-plugin");
const cwplg = require("clean-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
// Kept here for when people want to analyze the size of what is imported. README.md contains more info.
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  entry: path.resolve(__dirname, "js/index.js"), // main js
  output: {
    path: path.resolve(__dirname, "dist"), // output folder
    publicPath: "/"
  },
  resolve: {
    alias: {
      // Be sure to update aliases in jest.config.js and tsconfig.json
      src: path.resolve(__dirname)
    },
    extensions: [".js", ".jsx", ".ts", ".tsx", ".css"]
  },
  module: {
    rules: [
      {
        test: /\.svg$/,
        loader: "svg-inline-loader"
      },
      {
        test: /\.(js|jsx|tsx|ts)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: [
              "@babel/preset-env",
              "@babel/preset-flow",
              ["@babel/preset-react", { runtime: "automatic" }],
              "@babel/preset-typescript"
            ]
          }
        }
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"]
      }
    ]
  },
  plugins: [
    // Kept here for when people want to analyze the size of what is imported. README.md contains more info.
    // new BundleAnalyzerPlugin({analyzerMode: "static"}),
    new WebpackManifestPlugin(),
    new HtmlWebpackPlugin({
      template: "./templates/index.html" // base html
    }),
    new MiniCssExtractPlugin({
      filename: "[name].[chunkhash].css"
    }),
    new cwplg.CleanWebpackPlugin({
      verbose: true
    })
  ],
  devServer: {
    static: path.resolve(__dirname, "static"),
    historyApiFallback: true
  },
  optimization: {
    minimize: true,
    minimizer: [new CssMinimizerPlugin({})]
  }
};
