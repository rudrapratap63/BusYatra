import { NextRequest, NextResponse } from "next/server";

import { AUTH_COOKIE_NAME } from "@/lib/auth-config";
import { serverGraphqlRequest } from "@/lib/server-graphql";
import type { AuthUser } from "@/types/auth";

type MeResult = {
  me: AuthUser | null;
};

const ME_QUERY = `
  query Me {
    me {
      id
      name
      email
      phoneNum
      role
      isVerified
    }
  }
`;

export async function GET(request: NextRequest) {
  const token = request.cookies.get(AUTH_COOKIE_NAME)?.value;

  if (!token) {
    return NextResponse.json({ user: null });
  }

  try {
    const data = await serverGraphqlRequest<MeResult>(ME_QUERY, undefined, token);
    return NextResponse.json({ user: data.me });
  } catch {
    const response = NextResponse.json({ user: null });
    response.cookies.delete(AUTH_COOKIE_NAME);
    return response;
  }
}
