import { HttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import {
  ApolloClient,
  InMemoryCache,
  registerApolloClient,
} from "@apollo/client-integration-nextjs";
import { cookies } from "next/headers";

import { AUTH_COOKIE_NAME, GRAPHQL_ENDPOINT } from "@/lib/auth-config";

export const { getClient, query, PreloadQuery } = registerApolloClient(() => {
  const authLink = setContext(async (_, { headers }) => {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;

    return {
      headers: {
        ...headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    };
  });

  const httpLink = new HttpLink({
    uri: GRAPHQL_ENDPOINT,
    fetchOptions: { cache: "no-store" },
  });

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: authLink.concat(httpLink),
  });
});
