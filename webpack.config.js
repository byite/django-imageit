const TerserPlugin = require("terser-webpack-plugin");
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const CopyWebpackPlugin = require("copy-webpack-plugin");

const path = require('path');

const opts = {
    rootDir: process.cwd(),
    staticSrcDir: './imageit/static/imageit/src/',
    devBuild: process.env.NODE_ENV !== "production"
};
module.exports = {
  entry: opts.staticSrcDir + 'js/index.tsx',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
      filename: 'js/imageit.js',
      path: path.resolve(__dirname, 'imageit/static/imageit/dist'),
  },
  plugins: [
    // Copy fonts and images to dist
    new CopyWebpackPlugin({
        patterns: [
            { from: opts.staticSrcDir + "/css", to: "css" },
            { from: opts.staticSrcDir + "/img", to: "img" }
        ]
    }),
  ],
  /*optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        parallel: true,
        terserOptions: {
          ecma: 5
        }
      }),
      new CssMinimizerPlugin(),
    ],
    runtimeChunk: false
  },*/
};