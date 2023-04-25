const path = require('path');

module.exports = {
  mode: 'development',
  entry: {
    account: './schemaserver/js/account.jsx',
    delete: './schemaserver/js/delete.jsx',
    create: './schemaserver/js/create.jsx',
    index: './schemaserver/js/index.jsx',
    login: './schemaserver/js/login.jsx',
    password: './schemaserver/js/password.jsx',
  },
  output: {
    path: path.join(__dirname, '/schemaserver/static/js/'),
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
