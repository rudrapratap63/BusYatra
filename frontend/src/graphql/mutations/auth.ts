import { graphql } from "@/graphql/generated";

export const LoginMutation = graphql(`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      __typename
      ... on AuthPayload {
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
`);

export const RegisterMutation = graphql(`
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      __typename
      ... on AuthPayload {
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
`);
