import { render, screen } from "@testing-library/react";
import GovernancaPage from "app/pages/governanca/index";
import React from "react";

test("renderiza logs corretamente em caso de sucesso", () => {
  render(<GovernancaPage />);
  expect(screen.getByText(/Logs de Governança/i)).toBeInTheDocument();
});

test("exibe fallback visual em erro de fetch de logs", async () => {
  jest.spyOn(global, "fetch").mockRejectedValueOnce(new Error("Erro de API"));
  render(<GovernancaPage />);
  expect(await screen.findByText(/Erro ao buscar logs/i)).toBeInTheDocument();
}); 