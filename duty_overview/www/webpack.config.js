const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  mode: "development",
  entry: path.resolve(__dirname, "js/index.js"), // main js
  output: {
    path: path.resolve(__dirname, "dist"), // output folder
    publicPath: "/",
  },
  resolve: {
    alias: { // Be sure to update aliases in jest.config.js and tsconfig.json
      src: path.resolve(__dirname),
    },
    extensions: [
      '.js',
      '.jsx',
      '.ts',
      '.tsx',
      '.css',
    ],
  },
  module: {
    rules: [
      {
        test: /\.svg$/,
        loader: 'svg-inline-loader'
      },
      {
        test: /\.(js|jsx|tsx|ts)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
             "presets": [
               "@babel/preset-env",
               "@babel/preset-flow",
               ["@babel/preset-react", {"runtime": "automatic"}],
               "@babel/preset-typescript",
             ]
          },
        },
      },
      {
        test: /\.css$/,
        use: [
          "style-loader",
          "css-loader", // for styles
        ],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./templates/index.html", // base html
    }),
  ],
  devServer: {
    static: path.resolve(__dirname, "static"),
    historyApiFallback: true,
  }
};
