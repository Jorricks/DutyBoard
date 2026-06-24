import {ChangeEvent, KeyboardEvent, useCallback, useEffect, useRef, useState} from "react";
import {Input, InputGroup, InputGroupProps, InputLeftElement, InputRightElement, Text} from "@chakra-ui/react";
import { FaSearch } from "@react-icons/all-files/fa/FaSearch";
import {useNavigate, useSearch} from "@tanstack/react-router";

type SearchBoxProps = {
  width?: InputGroupProps["width"];
};

export default function SearchBox({width = "220px"}: SearchBoxProps) {
  const navigate = useNavigate();
  const search = useSearch({strict: false}) as {search?: string};
  const inputRef = useRef<HTMLInputElement>(null);
  const [searchValue, setSearchValue] = useState(search.search ?? "");

  const navigateWithSearch = useCallback((value: string) => {
    void navigate({
      replace: true,
      search: (previous) => {
        const next = {...previous};

        if (value.trim()) {
          return {...next, search: value};
        }

        delete next.search;
        return next;
      }
    });
  }, [navigate]);

  useEffect(() => {
    setSearchValue(search.search ?? "");
  }, [search.search]);

  useEffect(() => {
    if (searchValue === (search.search ?? "")) {
      return;
    }

    const timeout = window.setTimeout(() => {
      navigateWithSearch(searchValue);
    }, 500);

    return () => window.clearTimeout(timeout);
  }, [navigateWithSearch, search.search, searchValue]);

  useEffect(() => {
    const onKeyDown = (event: globalThis.KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const isTyping = target instanceof HTMLInputElement
        || target instanceof HTMLTextAreaElement
        || target?.isContentEditable;

      if (event.key === "/" && !isTyping && !event.metaKey && !event.ctrlKey && !event.altKey) {
        event.preventDefault();
        inputRef.current?.focus();
      }

      if (event.key === "Escape" && !isTyping && search.search) {
        setSearchValue("");
        navigateWithSearch("");
      }
    };

    window.addEventListener("keydown", onKeyDown);

    return () => window.removeEventListener("keydown", onKeyDown);
  }, [navigateWithSearch, search.search]);

  const onSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const onSearchKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Escape") {
      return;
    }

    event.currentTarget.blur();
    setSearchValue("");
    navigateWithSearch("");
  };

  return (
    <InputGroup width={width} size="sm">
      <InputLeftElement color="gray.500" pointerEvents="none">
        <FaSearch />
      </InputLeftElement>
      {!searchValue ? (
        <InputRightElement alignItems="center" display="flex" pointerEvents="none">
          <Text color="gray.500" fontSize="sm" lineHeight="1" transform="translateY(-1px)">/</Text>
        </InputRightElement>
      ) : null}
      <Input
        aria-label="Search"
        bg="rgba(255, 255, 255, 0.8)"
        border="none"
        borderRadius="md"
        color="gray.900"
        onChange={onSearchChange}
        onKeyDown={onSearchKeyDown}
        placeholder="Search duty teams"
        ref={inputRef}
        value={searchValue}
        _focusVisible={{
          boxShadow: "0 0 0 2px rgba(255, 255, 255, 0.7)"
        }}
        _placeholder={{color: "gray.500"}}
      />
    </InputGroup>
  );
}
