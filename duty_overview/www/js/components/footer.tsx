import {
  Box,
  chakra,
  Container,
  Stack,
  Text,
  useColorModeValue,
  VisuallyHidden
} from "@chakra-ui/react";
import { FaGithub } from "react-icons/fa";
import { ReactNode } from "react";
import CompanyLogo from "./companyLogo";
import { useGetSchedule } from "../api";
import { Link } from "@tanstack/react-router";

const SocialButton = ({
  children,
  label,
  href
}: {
  children: ReactNode;
  label: string;
  href: string;
}) => {
  return (
    <chakra.button
      bg={useColorModeValue("blackAlpha.100", "whiteAlpha.100")}
      rounded={"full"}
      w={8}
      h={8}
      cursor={"pointer"}
      as={"a"}
      href={href}
      display={"inline-flex"}
      alignItems={"center"}
      justifyContent={"center"}
      transition={"background 0.3s ease"}
      _hover={{
        bg: useColorModeValue("blackAlpha.200", "whiteAlpha.200")
      }}
    >
      <VisuallyHidden>{label}</VisuallyHidden>
      {children}
    </chakra.button>
  );
};

export default function Footer() {
  const {
    data: { config },
    isLoading
  } = useGetSchedule();

  return (
    <Box bg={config.backgroundColor} color={config.textColor}>
      <Container as={Stack} maxW={"6xl"} py={4} spacing={4} justify={"center"} align={"center"}>
        <CompanyLogo maxWidth={250} maxHeight={150} />
        <Stack direction={"row"} spacing={6}>
          {config.categories.map((aCategory: string) => (
            <Link
              to="/$category"
              params={{ category: aCategory }}
              activeProps={{ className: "font-bold" }}
              key={"footer" + aCategory}
            >
              {aCategory}
            </Link>
          ))}
        </Stack>
        <Container
          as={Stack}
          justify={{ base: "center", md: "space-between" }}
          align={{ base: "center", md: "center" }}
        >
          <Text>All dates & times are in your local timezone; {config.timezone}</Text>
        </Container>
      </Container>

      <Box
        borderTopWidth={1}
        borderStyle={"solid"}
        borderColor={useColorModeValue("gray.200", "gray.700")}
      >
        <Container
          as={Stack}
          maxW={"6xl"}
          py={4}
          direction={{ base: "column", md: "row" }}
          spacing={4}
          justify={{ base: "center", md: "space-between" }}
          align={{ base: "center", md: "center" }}
        >
          <Text>© 2022 All rights reserved</Text>
          <Stack direction={"row"} spacing={6}>
            <SocialButton label={"Github"} href={"https://github.com/Jorricks/DutyOverview"}>
              <FaGithub />
            </SocialButton>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}
