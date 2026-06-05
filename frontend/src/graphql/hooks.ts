"use client";

import { useMutation, useQuery } from "@apollo/client/react";

import { LoginMutation, RegisterMutation } from "@/graphql/mutations/auth";
import { MeQuery } from "@/graphql/queries/me";

export function useMeQuery() {
  return useQuery(MeQuery);
}

export function useLoginMutation() {
  return useMutation(LoginMutation);
}

export function useRegisterMutation() {
  return useMutation(RegisterMutation);
}
