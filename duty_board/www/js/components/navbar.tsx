import {
  Box,
  Flex,
  HStack,
  IconButton,
  Button,
  Menu,
  useDisclosure,
  useColorModeValue,
  Stack,
  Text,
} from "@chakra-ui/react";
import { AiFillGithub } from "@react-icons/all-files/ai/AiFillGithub";
import { GiHamburgerMenu } from "@react-icons/all-files/gi/GiHamburgerMenu";
import { IoCloseOutline } from "@react-icons/all-files/io5/IoCloseOutline";
import { GrUserAdmin } from "@react-icons/all-files/gr/GrUserAdmin";
import CompanyLogo from "./companyLogo";
import { useGetSchedule } from "../api";
import {Link, useMatch} from "@tanstack/react-router";
import ExternalLink from "./externalLink";
import SearchBox from "./searchBox";

const NavLink = ({ category }: { category: string }) => (
  <Link to="/$category" params={{ category }} search={(previous) => {
    const next = {...previous};
    delete next.search;
    return next;
  }} activeProps={{ className: "font-bold" }}>
    <Box
      px={2}
      py={1}
      rounded={"md"}
      _hover={{
        textDecoration: "none",
        bg: useColorModeValue("gray.200", "gray.700")
      }}
    >
      {category}
    </Box>
  </Link>
);

export default function Navbar() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    data: { config },
    isLoading
  } = useGetSchedule();

  const data = useMatch("/$category", { strict: false });
  const enabledCategory = data && data.params && data.params.category !== undefined
    ? decodeURI(data.params.category)
    : config.categories[0];

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
          </HStack>
          <Flex alignItems={"center"} gap={4} ml={6} mr={"20px"}>
            <Box display={{ base: "none", md: "block" }}>
              <SearchBox />
            </Box>
            {config.gitRepositoryUrl &&
              <Menu>
                <ExternalLink href={config.gitRepositoryUrl} external={true}>
                  <Button
                      leftIcon={<AiFillGithub color={config.textColor} fontSize={"30px"}/>}
                      colorScheme='teal'
                      variant='outline'
                  >
                    <Text color={config.textColor}>Repo</Text>
                  </Button>
                </ExternalLink>
              </Menu>
            }
            {config.enableAdminButton &&
              <Menu>
                <ExternalLink href={import.meta.env.VITE_API_ADDRESS + "admin/"} external={true}>
                  <Button
                      leftIcon={<GrUserAdmin color={config.textColor} fontSize={"25px"} />}
                      colorScheme='teal'
                      variant='outline'
                  >
                    <Text color={config.textColor}>Admin</Text>
                  </Button>
                </ExternalLink>
              </Menu>
            }
          </Flex>
        </Flex>

        <Box
          display={{ base: "none", md: "block" }}
          overflowX="auto"
          pb={3}
          sx={{
            "&::-webkit-scrollbar": {display: "none"},
            scrollbarWidth: "none"
          }}
        >
          <HStack as={"nav"} spacing={4} minW="max-content">
            {config.categories.map((category: string) => (
              category === enabledCategory ? (
                <Box key={"normal" + category} textDecoration='underline'><NavLink category={category} /></Box>
              ) : (
                <Box key={"normal" + category}><NavLink category={category} /></Box>
              )
            ))}
          </HStack>
        </Box>

        {isOpen ? (
          <Box pb={4} display={{ md: "none" }}>
            <Stack as={"nav"} spacing={4}>
              {config.categories.map((category: string) => (
                <NavLink category={category} key={"mobile" + category} />
              ))}
              <SearchBox width="100%" />
            </Stack>
          </Box>
        ) : null}
      </Box>
    </>
  );
}
