import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT ?? "http://localhost:8000/graphql",
  documents: ["src/**/*.{ts,tsx}", "!src/graphql/generated/**/*"],
  generates: {
    "./src/graphql/generated/": {
      preset: "client",
      presetConfig: {
        gqlTagName: "graphql",
      },
    },
  },
  ignoreNoDocuments: true,
};

export default config;
