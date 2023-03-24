const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  mode: "development",
  entry: "./src/index.tsx",
  devtool: "inline-source-map",
  devServer: {
    static: "./dist",
    historyApiFallback: true,
  },
  resolve: {
    extensions: [".js", ".jsx", ".ts", ".tsx"],
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: "Buzz @ VIB Technology Training",
      template: "src/index.html",
      favicon: "src/buzz.svg",
    }),
    new webpack.DefinePlugin({
      SERVICE_URL: JSON.stringify("http://localhost:8000"),
      WEBSOCKET_URL: JSON.stringify("ws://localhost:8000/ws"),
    }),
  ],
  output: {
    path: path.resolve(__dirname, "./dist"),
    filename: "[name].bundle.js",
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/i,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: "asset/resource",
      },
    ],
  },
};
