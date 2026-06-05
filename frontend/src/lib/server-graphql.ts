import { GRAPHQL_ENDPOINT } from "@/lib/auth-config";

type GraphQLErrorResponse = {
  errors?: { message: string }[];
};

export async function serverGraphqlRequest<TData>(
  query: string,
  variables?: Record<string, unknown>,
  token?: string,
): Promise<TData> {
  const response = await fetch(GRAPHQL_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: "no-store",
    body: JSON.stringify({ query, variables }),
  });

  const result = (await response.json()) as GraphQLErrorResponse & {
    data?: TData;
  };

  if (!response.ok || result.errors?.length || !result.data) {
    throw new Error(result.errors?.[0]?.message ?? "GraphQL request failed");
  }

  return result.data;
}
