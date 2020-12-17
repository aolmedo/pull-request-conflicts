package main;

import java.io.*;
import java.util.Arrays;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;

public class Matrix {
	
	public Matrix(int size) {
		this.size = size;
		content = new int[size][size];
		columnTags = new int[size];
		rowTags = new int[size];
		
		for (int i=0;i<size;i++)
		{
			columnTags[i]=i;
			rowTags[i]=i;
		}
	}

	int size;
	
	int[][] content;
	int[] columnTags;
	int[] rowTags;
	
	int edgeNumber=0;
	
	List<List<Integer>> colorSetList;
	

	private int[] processLine(String[] values) {
		int[] intarray=new int[values.length];
		int i=0;
		for(String str:values){
			intarray[i]=Integer.parseInt(str.trim());
			i++;
		}
		return intarray;
	}

	public void import_matrix()
	{
		try (BufferedReader br = new BufferedReader(new FileReader("matrix.csv"))) {
			String line;
			line = br.readLine();
			int[] values = this.processLine(line.split(","));
			
			size = values.length-1;
			content = new int[size][size];
			columnTags = new int[size];
			rowTags = new int[size];

			columnTags = Arrays.copyOfRange(values, 1, values.length);
			int i = 0;
			while ((line = br.readLine()) != null) {
				//System.out.print(i);
				values = this.processLine(line.split(","));
				rowTags[i] = Arrays.copyOfRange(values, 0, 1)[0];
				content[i] = Arrays.copyOfRange(values, 1, values.length);
				i++;
	    		}
		}
		catch (IOException ex)  
		{
			System.out.print("Archivo no encontrado");
		}
	}

	public void display()
	{
		System.out.print("  ");
		for (int i=0;i<size;i++)
			System.out.print(columnTags[i]+" ");
		System.out.println("");
		for (int i=0;i<size;i++)
		{
			System.out.print(rowTags[i]+" ");
			for (int j=0;j<size;j++)
			{
				System.out.print(content[i][j]);
				System.out.print(" ");
			}
			System.out.println("");
		}
	}
	
	public void randomInit()
	{
		int flipNumber = (size*size)/10;
		
		Random r = new Random();
		
		for (int i=0;i<flipNumber;i++)
		{
			int row=r.nextInt(size);
			int column=r.nextInt(size);
			
			if (row!=column)
			{
				content[row][column]=1;
				content[column][row]=1;
				edgeNumber++;
			}	
		}
	}
	
	public void solve()
	{
		Model m = new Model("coloration");
		
		//int maxColor = (size*size)/(size*size-2*edgeNumber);
		
		IntVar colors = m.intVar("colors",0,size-1);
		
		IntVar[] vector = m.intVarArray("vector",size,0,size-1);
		
		for (int i=0;i<size;i++)
		{
			m.arithm(vector[i],"<=",colors).post();
			for (int j=i;j<size;j++)
			{
				if (content[i][j]==1) m.arithm(vector[i],"!=",vector[j]).post();
			}
		}
		
		m.setObjective(Model.MINIMIZE,colors);
		
		Solver solver = m.getSolver();
		
		solver.makeCompleteStrategy(true);
		
		if(solver.solve()) 
			{
			//System.out.println(colors);
//			for (int i=0;i<size;i++)
//				System.out.println(vector[i]+" ");
//			System.out.println("");
			
			colorSetList = new ArrayList<List<Integer>>();
			
			for (int i=0;i<=colors.getValue();i++)
			  colorSetList.add(i,new ArrayList<Integer>());
			
			for (int i=0;i<size;i++)
				colorSetList.get(vector[i].getValue()).add(i);
			}
		else 
			{ 
			//if (solver.isSearchCompleted()) System.out.println("No solution !");
		    //else System.out.println(colors);
			System.exit(0);
			}
	}
	
	public void reorder()
	{
		int currentIndex = 0;
		//System.out.println("colorsetlist size "+colorSetList.size());
		
		for (int i=0;i<colorSetList.size();i++)
		{
			List<Integer> currentColorSet = colorSetList.get(i);
			//System.out.println("color size "+currentColorSet.size());
			
			for (int j=0;j<currentColorSet.size();j++)
			{
				//System.out.println("current index "+currentIndex);
				int movedVector = currentColorSet.get(j);
				int movingColumn = getColumnIndex(currentIndex,movedVector);
				int movingRow = getRowIndex(currentIndex,movedVector);
				swapColumns(currentIndex,movingColumn);
				swapRows(currentIndex,movingRow);
				currentIndex++;
			}
		}	
	}
	
	private void swapRows(int currentIndex, int movingRow) {
		// TODO Auto-generated method stub
		if (currentIndex==movingRow) return;
		
		int buffer;
		
		for (int i=0;i<size;i++)
		{
			buffer = content[currentIndex][i];
			content[currentIndex][i]=content[movingRow][i];
			content[movingRow][i]=buffer;
		}
		buffer = rowTags[currentIndex];
		rowTags[currentIndex]=rowTags[movingRow];
		rowTags[movingRow]=buffer;
	}

	private void swapColumns(int currentIndex, int movingColumn) {
		// TODO Auto-generated method stub
		if (currentIndex==movingColumn) return;
		
		int buffer;
		
		for (int i=0;i<size;i++)
		{
			buffer = content[i][currentIndex];
			content[i][currentIndex]=content[i][movingColumn];
			content[i][movingColumn]=buffer;
		}
		buffer = columnTags[currentIndex];
		columnTags[currentIndex]=columnTags[movingColumn];
		columnTags[movingColumn]=buffer;
	}

	public int getRowIndex(int startIndex,int row)
	{
		int i=startIndex;
		for (;i<size;i++)
			if (rowTags[i]==row) return i;
		return -1;
	}
	
	public int getColumnIndex(int startIndex, int column)
	{
		int i=startIndex;
		for (;i<size;i++)
			if (columnTags[i]==column) return i;
		return -1;
	}
	
	public void displaycolorSets()
	{
		for (int i=0;i<colorSetList.size();i++)
		{
			//System.out.print("set "+i+": ");
			for (int j=0;j<colorSetList.get(i).size();j++)
				if (j==colorSetList.get(i).size()-1){
					System.out.print(rowTags[colorSetList.get(i).get(j)]);
				}else{
					System.out.print(rowTags[colorSetList.get(i).get(j)]+",");
				}
			System.out.println("");
		}
	}

}
