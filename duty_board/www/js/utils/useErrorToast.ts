import { useToast } from "@chakra-ui/react";
import type { ReactNode } from "react";
import axios from "axios";

type ErrorType = Error | string | null;

export const getErrorDescription = (error?: ErrorType, fallbackMessage?: string) => {
  if (typeof error === "string") return error;
  if (error instanceof Error) {
    let { message } = error;
    if (axios.isAxiosError(error)) {
      message = error.response?.data?.detail || error.response?.data || error.message;
    }
    return message;
  }
  return fallbackMessage || "Something went wrong.";
};

const getErrorTitle = (error: Error) => error.message || "Error";

const useErrorToast = () => {
  const toast = useToast();
  // Add an error prop and handle it as a description
  return ({ error, title, ...rest }: { error: Error; title?: ReactNode }) => {
    toast({
      ...rest,
      status: "error",
      title: title || getErrorTitle(error),
      description: getErrorDescription(error).slice(0, 500)
    });
  };
};

export default useErrorToast;
