FROM node:16

# Set working directory
WORKDIR /usr/src/frontend/crawler

RUN chown -R node:node /usr/src/frontend/crawler

# Add `/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/frontend/crawler/node_modules/.bin:$PATH

# install app dependencies
COPY --chown=node:node ./crawler/package.json ./
COPY --chown=node:node ./crawler/package-lock.json ./

RUN npm install --silent
RUN npm install react-scripts@3.4.1 -g --silent

# Add app
COPY --chown=node:node ./crawler ./

USER node

# Start the app
CMD ["npm", "start"]