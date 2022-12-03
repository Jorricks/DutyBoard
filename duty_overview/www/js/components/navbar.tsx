import { ReactNode } from "react";
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Button,
  Menu,
  MenuButton,
  useDisclosure,
  useColorModeValue,
  Stack
} from "@chakra-ui/react";
import { GiHamburgerMenu } from "@react-icons/all-files/gi/GiHamburgerMenu";
import { IoCloseOutline } from "@react-icons/all-files/io5/IoCloseOutline";
import { GrUserAdmin } from "@react-icons/all-files/gr/GrUserAdmin";
import CompanyLogo from "./companyLogo";
import { useGetSchedule } from "../api";
import { Link } from "@tanstack/react-router";

const NavLink = ({ children }: { children: ReactNode }) => (
  <Link to="/$category" params={{ category: children }} activeProps={{ className: "font-bold" }}>
    <Box
      px={2}
      py={1}
      rounded={"md"}
      _hover={{
        textDecoration: "none",
        bg: useColorModeValue("gray.200", "gray.700")
      }}
    >
      {children}
    </Box>
  </Link>
);

export default function Navbar() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    data: { config },
    isLoading
  } = useGetSchedule();

  return (
    <>
      <Box bg={config.backgroundColor} color={config.textColor} px={4}>
        <Flex h={16} alignItems={"center"} justifyContent={"space-between"}>
          <IconButton
            size={"md"}
            icon={isOpen ? <IoCloseOutline /> : <GiHamburgerMenu />}
            aria-label={"Open Menu"}
            display={{ md: "none" }}
            onClick={isOpen ? onClose : onOpen}
          />
          <HStack spacing={8} alignItems={"center"}>
            <CompanyLogo maxWidth={300} maxHeight={40} />
            <HStack as={"nav"} spacing={4} display={{ base: "none", md: "flex" }}>
              {config.categories.map((category: string) => (
                <NavLink key={"normal" + category}>{category}</NavLink>
              ))}
            </HStack>
          </HStack>
          <Flex alignItems={"center"}>
            <Menu>
              <MenuButton as={Button} rounded={"full"} variant={"link"} cursor={"pointer"} minW={0}>
                <GrUserAdmin />
              </MenuButton>
            </Menu>
          </Flex>
        </Flex>

        {isOpen ? (
          <Box pb={4} display={{ md: "none" }}>
            <Stack as={"nav"} spacing={4}>
              {config.categories.map((category: string) => (
                <NavLink key={"mobile" + category}>{category}</NavLink>
              ))}
            </Stack>
          </Box>
        ) : null}
      </Box>
    </>
  );
}
