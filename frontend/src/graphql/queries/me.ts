import { graphql } from "@/graphql/generated";

export const MeQuery = graphql(`
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
`);
