import { GraphQLClient } from 'graphql-request'

const GRAPHQL_URL = import.meta.env.VITE_GRAPHQL_URL || 'http://localhost:8000/graphql'

export const graphqlClient = new GraphQLClient(GRAPHQL_URL)

export default graphqlClient

