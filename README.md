# progeficaz-projeto2

Requisitos 
1. Devem haver rotas para:
  1.2. Listar todos os imóveis com todos os seus atributos;
  1.3. Listar um imóvel específico pelo seu id com todos os seus atributos;
  1.4. Adicionar um novo imóvel;
  1.5. Atualizar um imóvel existente;
  1.6. Remover um imóvel existente;
  1.7. Buscar imóveis por tipo (casa, apartamento, terreno, etc) com todos os seus atributos;
  1.8. Buscar imóveis por cidade com todos os seus atributos;

2. Devem haver testes automatizados para todas as rotas.
3. O servidor deve ser desenvolvido utilizando o framework Flask.
4. O servidor deve utilizar o banco de dados MySQL hospedado na plataforma Aiven.
5. O projeto deve utilizar os princípios de TDD.
6. O projeto deve ter o deploy feito em um EC2 na AWS.
7. Para gerar o banco de dados, utilize o script disponível aqui

```
docker cp banco.sql mysql-imoveis:/banco.sql
docker exec mysql-imoveis sh -c "mysql -uroot -psenha123 imoveis_db < /banco.sql"
docker exec mysql-imoveis mysql -uroot -psenha123 imoveis_db -e "SELECT * FROM imoveis;"
```

```
git commit -m "MENSAGEM

Co-authored-by: Daniel Vinícius <daniel.vinicius.sviana@gmail.com>
Co-authored-by: Pedro Souza <pedrohbzs@al.insper.edu.br>"
```