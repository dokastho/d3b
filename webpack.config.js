const path = require('path');

module.exports = {
  mode: 'development',
  entry: {
    account: './authserver/js/account.jsx',
    delete: './authserver/js/delete.jsx',
    create: './authserver/js/create.jsx',
    index: './authserver/js/index.jsx',
    login: './authserver/js/login.jsx',
    password: './authserver/js/password.jsx',
  },
  output: {
    path: path.join(__dirname, '/authserver/static/js/'),
    filename: '[name].bundle.js',
  },
  module: {
    rules: [
      {
        // Test for js or jsx files
        test: /\.jsx?$/,
        // Exclude external modules from loader tests
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env', '@babel/preset-react'],
          plugins: ['@babel/transform-runtime'],
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
