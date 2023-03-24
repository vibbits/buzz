const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

module.exports = {
  mode: "production",
  entry: "./src/index.tsx",
  devtool: "source-map",
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
      SERVICE_URL: JSON.stringify("https://buzz.vib.be/api/v1"),
      WEBSOCKET_URL: JSON.stringify("wss://buzz.vib.be/api/v1/ws"),
    }),
    new MiniCssExtractPlugin(),
  ],
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin(), new CssMinimizerPlugin()],
    providedExports: true,
    sideEffects: true,
    concatenateModules: true,
    usedExports: true,
  },
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
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: "asset/resource",
      },
    ],
  },
};
