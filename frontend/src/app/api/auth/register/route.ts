import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, AUTH_COOKIE_OPTIONS } from "@/lib/auth-config";
import { serverGraphqlRequest } from "@/lib/server-graphql";
import type { AuthUser, RegisterCredentials } from "@/types/auth";

type RegisterResult = {
  register: {
    __typename: "AuthPayload" | "ValidationError";
    token?: string | null;
    user?: AuthUser;
    message?: string;
  };
};

const REGISTER_MUTATION = `
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
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
    const credentials = (await request.json()) as RegisterCredentials;
    const data = await serverGraphqlRequest<RegisterResult>(REGISTER_MUTATION, {
      input: credentials,
    });

    if (data.register.__typename === "ValidationError") {
      return NextResponse.json(
        { message: data.register.message ?? "Unable to create account" },
        { status: 400 },
      );
    }

    if (!data.register.token || !data.register.user) {
      return NextResponse.json(
        { message: "Registration response was incomplete" },
        { status: 502 },
      );
    }

    const response = NextResponse.json({ user: data.register.user });
    response.cookies.set(
      AUTH_COOKIE_NAME,
      data.register.token,
      AUTH_COOKIE_OPTIONS,
    );
    return response;
  } catch (error) {
    return NextResponse.json(
      {
        message:
          error instanceof Error ? error.message : "Unable to create account",
      },
      { status: 500 },
    );
  }
}
