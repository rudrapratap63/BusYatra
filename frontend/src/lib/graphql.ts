const GRAPHQL_ENDPOINT =
  process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT ?? "http://localhost:8000/graphql";

type GraphQLErrorResponse = {
  errors?: { message: string }[];
};

export async function graphqlRequest<TData>(
  query: string,
  variables?: Record<string, unknown>,
): Promise<TData> {
  const response = await fetch(GRAPHQL_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ query, variables }),
  });

  const result = (await response.json()) as GraphQLErrorResponse & {
    data?: TData;
  };

  if (!response.ok || result.errors?.length || !result.data) {
    throw new Error(result.errors?.[0]?.message ?? "Something went wrong");
  }

  return result.data;
}
