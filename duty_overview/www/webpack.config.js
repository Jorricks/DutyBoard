const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
module.exports = {
  mode: "development",
  entry: "/src/index.js", // main js
  output: {
    path: path.resolve(__dirname, "dist"), // output folder
    publicPath: "/",
  },
  module: {
    rules: [
      {
        test: /\.svg$/,
        loader: 'svg-inline-loader'
      },
      {
        test: /\.?js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
             "presets": [
                 "@babel/preset-env",
                ["@babel/preset-react", {"runtime": "automatic"}]
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
  }
};
