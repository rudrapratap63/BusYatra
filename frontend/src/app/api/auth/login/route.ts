import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, AUTH_COOKIE_OPTIONS } from "@/lib/auth-config";
import { serverGraphqlRequest } from "@/lib/server-graphql";
import type { AuthUser, LoginCredentials } from "@/types/auth";

type LoginResult = {
  login: {
    __typename: "AuthPayload" | "ValidationError";
    token?: string | null;
    user?: AuthUser;
    message?: string;
  };
};

const LOGIN_MUTATION = `
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      __typename
      ... on AuthPayload {
        token
        user {
          id
          name
          email
          phoneNum
          role
          isVerified
        }
      }
      ... on ValidationError {
        message
      }
    }
  }
`;

export async function POST(request: Request) {
  try {
    const credentials = (await request.json()) as LoginCredentials;
    const data = await serverGraphqlRequest<LoginResult>(LOGIN_MUTATION, {
      input: credentials,
    });

    if (data.login.__typename === "ValidationError") {
      return NextResponse.json(
        { message: data.login.message ?? "Invalid email or password" },
        { status: 401 },
      );
    }

    if (!data.login.token || !data.login.user) {
      return NextResponse.json(
        { message: "Login response was incomplete" },
        { status: 502 },
      );
    }

    const response = NextResponse.json({ user: data.login.user });
    response.cookies.set(
      AUTH_COOKIE_NAME,
      data.login.token,
      AUTH_COOKIE_OPTIONS,
    );
    return response;
  } catch (error) {
    return NextResponse.json(
      { message: error instanceof Error ? error.message : "Unable to sign in" },
      { status: 500 },
    );
  }
}
