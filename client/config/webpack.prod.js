const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  mode: "production",
  entry: "./src/index.tsx",
  devtool: "inline-source-map",
  resolve: {
    extensions: [".js", ".jsx", ".ts", ".tsx"],
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: "VIB Training: Buzz",
      template: "src/index.html",
      favicon: "src/buzz.svg",
    }),
    new webpack.DefinePlugin({
      SERVICE_URL: JSON.stringify("https://buzz.vib.be/api/v1"),
      WEBSOCKET_URL: JSON.stringify("wss://buzz.vib.be/api/v1/ws"),
    }),
  ],
  output: {
    path: path.resolve(__dirname, "../dist"),
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
